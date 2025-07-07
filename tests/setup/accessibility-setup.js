// Accessibility testing setup
import { configureAxe } from 'jest-axe'

// Configure axe-core for accessibility testing
const axe = configureAxe({
  rules: {
    // Disable color-contrast rule for now (we'll test it separately)
    'color-contrast': { enabled: false },
    // Enable other important rules
    'aria-allowed-attr': { enabled: true },
    'aria-hidden-focus': { enabled: true },
    'aria-labelledby': { enabled: true },
    'aria-required-attr': { enabled: true },
    'aria-required-children': { enabled: true },
    'aria-required-parent': { enabled: true },
    'aria-roles': { enabled: true },
    'aria-valid-attr': { enabled: true },
    'aria-valid-attr-value': { enabled: true },
    'button-name': { enabled: true },
    'bypass': { enabled: true },
    'focus-order-semantics': { enabled: true },
    'form-field-multiple-labels': { enabled: true },
    'frame-title': { enabled: true },
    'html-has-lang': { enabled: true },
    'html-lang-valid': { enabled: true },
    'image-alt': { enabled: true },
    'input-image-alt': { enabled: true },
    'keyboard': { enabled: true },
    'label': { enabled: true },
    'landmark-banner-is-top-level': { enabled: true },
    'landmark-complementary-is-top-level': { enabled: true },
    'landmark-contentinfo-is-top-level': { enabled: true },
    'landmark-main-is-top-level': { enabled: true },
    'landmark-no-duplicate-banner': { enabled: true },
    'landmark-no-duplicate-contentinfo': { enabled: true },
    'landmark-one-main': { enabled: true },
    'link-name': { enabled: true },
    'list': { enabled: true },
    'listitem': { enabled: true },
    'page-has-heading-one': { enabled: true },
    'region': { enabled: true },
    'scope-attr-valid': { enabled: true },
    'server-side-image-map': { enabled: true },
    'skip-link': { enabled: true },
    'tabindex': { enabled: true },
    'table-fake-caption': { enabled: true },
    'td-headers-attr': { enabled: true },
    'th-has-data-cells': { enabled: true },
    'valid-lang': { enabled: true },
  },
  tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
})

// Make axe available globally for tests
global.axe = axe

// Helper function for accessibility testing
global.testAccessibility = async (container) => {
  const results = await axe(container)
  expect(results).toHaveNoViolations()
  return results
}

// Mock screen reader announcements
global.mockScreenReader = {
  announcements: [],
  announce: function(message) {
    this.announcements.push({
      message,
      timestamp: Date.now(),
    })
  },
  clear: function() {
    this.announcements = []
  },
  getAnnouncements: function() {
    return [...this.announcements]
  },
}

// Mock aria-live regions
const originalSetAttribute = Element.prototype.setAttribute
Element.prototype.setAttribute = function(name, value) {
  if (name === 'aria-live' && value) {
    // Track aria-live region updates
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' || mutation.type === 'characterData') {
          global.mockScreenReader.announce(this.textContent)
        }
      })
    })
    observer.observe(this, { childList: true, subtree: true, characterData: true })
  }
  return originalSetAttribute.call(this, name, value)
}

console.log('✅ Accessibility testing setup complete')
