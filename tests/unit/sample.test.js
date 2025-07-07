/**
 * Sample test to verify Jest configuration is working
 */

describe('Jest Configuration Test', () => {
  test('should run basic JavaScript test', () => {
    expect(1 + 1).toBe(2)
  })

  test('should handle async operations', async () => {
    const result = await Promise.resolve('test')
    expect(result).toBe('test')
  })

  test('should mock functions', () => {
    const mockFn = jest.fn()
    mockFn('test')
    expect(mockFn).toHaveBeenCalledWith('test')
  })

  test('should have access to global test utilities', () => {
    expect(global.testUtils).toBeDefined()
    expect(typeof global.testUtils.waitFor).toBe('function')
    expect(typeof global.testUtils.createMockEvent).toBe('function')
  })
})
