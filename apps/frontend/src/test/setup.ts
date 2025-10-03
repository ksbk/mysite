/**
 * Test setup configuration for Vitest
 * Sets up DOM environment and global utilities for testing
 */

import { beforeEach, vi } from "vitest";

// Mock CSRF token for tests
Object.defineProperty(window, "csrfToken", {
  value: "test-csrf-token",
  writable: true,
});

// Reset before each test
beforeEach(() => {
  vi.clearAllMocks();
});
