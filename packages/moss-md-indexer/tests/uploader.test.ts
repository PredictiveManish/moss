import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import type { MossCreds, MossDocument } from '../src/types.js'

// Use vi.hoisted to ensure mocks are available when vi.mock is hoisted
const mocks = vi.hoisted(() => {
  return {
    mockGetIndex: vi.fn(),
    mockCreateIndex: vi.fn(),
    mockAddDocs: vi.fn(),
    mockDeleteDocs: vi.fn(),
    mockDeleteIndex: vi.fn(),
    mockGetDocs: vi.fn(),
  }
})

// Mock @moss-dev/moss - MossClient must be a class/constructor
vi.mock('@moss-dev/moss', () => {
  return {
    MossClient: class MockMossClient {
      projectId: string
      projectKey: string

      constructor(projectId: string, projectKey: string) {
        this.projectId = projectId
        this.projectKey = projectKey
      }

      getIndex = mocks.mockGetIndex
      createIndex = mocks.mockCreateIndex
      addDocs = mocks.mockAddDocs
      deleteDocs = mocks.mockDeleteDocs
      deleteIndex = mocks.mockDeleteIndex
      getDocs = mocks.mockGetDocs
    }
  }
})

// Import after mock is set up
import { uploadDocuments, deleteIndex } from '../src/uploader.js'

describe('uploadDocuments', () => {
  const creds: MossCreds = {
    projectId: 'test-project',
    projectKey: 'test-key',
    indexName: 'test-index',
    modelName: 'moss-minilm'
  }

  const mockDocuments: MossDocument[] = [
    { id: 'doc-1', text: 'Test document 1', metadata: { title: 'Test 1' } as any },
    { id: 'doc-2', text: 'Test document 2', metadata: { title: 'Test 2' } as any },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(console, 'log').mockImplementation(() => {})
    vi.spyOn(console, 'warn').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('when index does not exist', () => {
    it('should create a new index', async () => {
      mocks.mockGetIndex.mockRejectedValue(new Error('Index not found'))
      mocks.mockCreateIndex.mockResolvedValue({ jobId: 'job-123' })

      await uploadDocuments(mockDocuments, creds)

      expect(mocks.mockGetIndex).toHaveBeenCalledWith('test-index')
      expect(mocks.mockCreateIndex).toHaveBeenCalledWith('test-index', mockDocuments, {
        modelId: 'moss-minilm'
      })
      expect(mocks.mockAddDocs).not.toHaveBeenCalled()
      expect(mocks.mockDeleteDocs).not.toHaveBeenCalled()
    })

    it('should return the create result', async () => {
      mocks.mockGetIndex.mockRejectedValue(new Error('Index not found'))
      const expectedResult = { jobId: 'job-123' }
      mocks.mockCreateIndex.mockResolvedValue(expectedResult)

      const result = await uploadDocuments(mockDocuments, creds)

      expect(result).toEqual(expectedResult)
    })
  })

  describe('when index exists', () => {
    it('should upsert documents and delete stale ones', async () => {
      mocks.mockGetIndex.mockResolvedValue({ name: 'test-index' })
      mocks.mockGetDocs.mockResolvedValue([
        { id: 'doc-1', text: 'Old version' },
        { id: 'doc-3', text: 'Stale document' },
      ])
      mocks.mockAddDocs.mockResolvedValue({ jobId: 'job-456' })
      mocks.mockDeleteDocs.mockResolvedValue({ jobId: 'job-789' })

      await uploadDocuments(mockDocuments, creds)

      expect(mocks.mockGetIndex).toHaveBeenCalledWith('test-index')
      expect(mocks.mockGetDocs).toHaveBeenCalledWith('test-index')
      expect(mocks.mockAddDocs).toHaveBeenCalledWith('test-index', mockDocuments, { upsert: true })
      expect(mocks.mockDeleteDocs).toHaveBeenCalledWith('test-index', ['doc-3'])
    })

    it('should not delete anything when no stale documents', async () => {
      mocks.mockGetIndex.mockResolvedValue({ name: 'test-index' })
      mocks.mockGetDocs.mockResolvedValue([
        { id: 'doc-1', text: 'Document 1' },
        { id: 'doc-2', text: 'Document 2' },
      ])
      mocks.mockAddDocs.mockResolvedValue({ jobId: 'job-456' })

      await uploadDocuments(mockDocuments, creds)

      expect(mocks.mockDeleteDocs).not.toHaveBeenCalled()
    })

    it('should delete all existing documents when new set is empty of old IDs', async () => {
      mocks.mockGetIndex.mockResolvedValue({ name: 'test-index' })
      mocks.mockGetDocs.mockResolvedValue([
        { id: 'old-1', text: 'Old document 1' },
        { id: 'old-2', text: 'Old document 2' },
      ])
      mocks.mockAddDocs.mockResolvedValue({ jobId: 'job-456' })
      mocks.mockDeleteDocs.mockResolvedValue({ jobId: 'job-789' })

      await uploadDocuments(mockDocuments, creds)

      expect(mocks.mockDeleteDocs).toHaveBeenCalledWith('test-index', ['old-1', 'old-2'])
    })
  })

  describe('when createIndex fails', () => {
    it('should throw error without deleting the index', async () => {
      mocks.mockGetIndex.mockRejectedValue(new Error('Index not found'))
      mocks.mockCreateIndex.mockRejectedValue(new Error('Network error'))

      await expect(uploadDocuments(mockDocuments, creds)).rejects.toThrow('Moss Upload Failed')
      expect(mocks.mockDeleteIndex).not.toHaveBeenCalled()
    })
  })

  describe('when document list is empty', () => {
    it('should do nothing and warn', async () => {
      const consoleWarnSpy = vi.spyOn(console, 'warn')

      await uploadDocuments([], creds)

      expect(consoleWarnSpy).toHaveBeenCalledWith('  ⚠️  No documents to upload.')
      expect(mocks.mockGetIndex).not.toHaveBeenCalled()
      expect(mocks.mockCreateIndex).not.toHaveBeenCalled()
    })
  })

  describe('with recreate option', () => {
    it('should delete index and create new one when recreate is true', async () => {
      mocks.mockDeleteIndex.mockResolvedValue(true)
      mocks.mockCreateIndex.mockResolvedValue({ jobId: 'job-123' })

      await uploadDocuments(mockDocuments, creds, { recreate: true })

      expect(mocks.mockDeleteIndex).toHaveBeenCalledWith('test-index')
      expect(mocks.mockCreateIndex).toHaveBeenCalledWith('test-index', mockDocuments, {
        modelId: 'moss-minilm'
      })
      expect(mocks.mockGetIndex).not.toHaveBeenCalled()
      expect(mocks.mockAddDocs).not.toHaveBeenCalled()
    })

    it('should handle deleteIndex failure gracefully', async () => {
      mocks.mockDeleteIndex.mockRejectedValue(new Error('Index not found'))
      mocks.mockCreateIndex.mockResolvedValue({ jobId: 'job-123' })

      await uploadDocuments(mockDocuments, creds, { recreate: true })

      expect(mocks.mockDeleteIndex).toHaveBeenCalledWith('test-index')
      expect(mocks.mockCreateIndex).toHaveBeenCalled()
    })
  })
})

describe('deleteIndex', () => {
  const creds: MossCreds = {
    projectId: 'test-project',
    projectKey: 'test-key',
    indexName: 'test-index',
    modelName: 'moss-minilm'
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(console, 'log').mockImplementation(() => {})
    vi.spyOn(console, 'warn').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should delete index successfully', async () => {
    mocks.mockDeleteIndex.mockResolvedValue(true)

    await deleteIndex(creds)

    expect(mocks.mockDeleteIndex).toHaveBeenCalledWith('test-index')
  })

  it('should handle index not found gracefully', async () => {
    mocks.mockDeleteIndex.mockRejectedValue(new Error('Index not found'))

    await deleteIndex(creds)

    expect(mocks.mockDeleteIndex).toHaveBeenCalledWith('test-index')
  })

  it('should log warning for other errors', async () => {
    const consoleWarnSpy = vi.spyOn(console, 'warn')
    mocks.mockDeleteIndex.mockRejectedValue(new Error('Permission denied'))

    await deleteIndex(creds)

    expect(consoleWarnSpy).toHaveBeenCalledWith(
      '  ⚠️  Could not delete index "test-index": Permission denied'
    )
  })
})
