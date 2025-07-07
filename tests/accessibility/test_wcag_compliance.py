"""
WCAG compliance and accessibility testing for CityPulse.
Tests for Web Content Accessibility Guidelines compliance, screen reader compatibility,
keyboard navigation, and color contrast.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Tuple
from playwright.async_api import async_playwright, Page
import json
import re
import colorsys
import logging

logger = logging.getLogger(__name__)


class ColorContrastAnalyzer:
    """Analyze color contrast for WCAG compliance."""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def get_relative_luminance(rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance for color contrast."""
        def normalize_color_component(c: int) -> float:
            c = c / 255.0
            if c <= 0.03928:
                return c / 12.92
            else:
                return pow((c + 0.055) / 1.055, 2.4)
        
        r, g, b = rgb
        r_norm = normalize_color_component(r)
        g_norm = normalize_color_component(g)
        b_norm = normalize_color_component(b)
        
        return 0.2126 * r_norm + 0.7152 * g_norm + 0.0722 * b_norm
    
    @staticmethod
    def calculate_contrast_ratio(color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors."""
        rgb1 = ColorContrastAnalyzer.hex_to_rgb(color1)
        rgb2 = ColorContrastAnalyzer.hex_to_rgb(color2)
        
        lum1 = ColorContrastAnalyzer.get_relative_luminance(rgb1)
        lum2 = ColorContrastAnalyzer.get_relative_luminance(rgb2)
        
        # Ensure lighter color is in numerator
        if lum1 > lum2:
            return (lum1 + 0.05) / (lum2 + 0.05)
        else:
            return (lum2 + 0.05) / (lum1 + 0.05)
    
    @staticmethod
    def meets_wcag_aa(contrast_ratio: float, is_large_text: bool = False) -> bool:
        """Check if contrast ratio meets WCAG AA standards."""
        if is_large_text:
            return contrast_ratio >= 3.0
        else:
            return contrast_ratio >= 4.5
    
    @staticmethod
    def meets_wcag_aaa(contrast_ratio: float, is_large_text: bool = False) -> bool:
        """Check if contrast ratio meets WCAG AAA standards."""
        if is_large_text:
            return contrast_ratio >= 4.5
        else:
            return contrast_ratio >= 7.0


class AccessibilityTester:
    """Comprehensive accessibility testing framework."""
    
    def __init__(self, page: Page):
        """Initialize accessibility tester with Playwright page."""
        self.page = page
        self.violations = []
    
    async def inject_axe_core(self):
        """Inject axe-core accessibility testing library."""
        # In a real implementation, you would inject the actual axe-core library
        # For testing purposes, we'll simulate the functionality
        await self.page.add_script_tag(content="""
            window.axe = {
                run: function(options) {
                    return Promise.resolve({
                        violations: [],
                        passes: [],
                        incomplete: [],
                        inapplicable: []
                    });
                }
            };
        """)
    
    async def run_axe_analysis(self) -> Dict[str, Any]:
        """Run axe-core accessibility analysis."""
        await self.inject_axe_core()
        
        # Run axe analysis
        results = await self.page.evaluate("""
            () => {
                return window.axe.run({
                    tags: ['wcag2a', 'wcag2aa', 'wcag21aa'],
                    rules: {
                        'color-contrast': { enabled: true },
                        'keyboard-navigation': { enabled: true },
                        'focus-management': { enabled: true },
                        'semantic-markup': { enabled: true },
                        'aria-labels': { enabled: true }
                    }
                });
            }
        """)
        
        return results
    
    async def check_keyboard_navigation(self) -> List[Dict[str, Any]]:
        """Test keyboard navigation accessibility."""
        issues = []
        
        # Get all interactive elements
        interactive_elements = await self.page.query_selector_all(
            'button, a, input, select, textarea, [tabindex], [role="button"], [role="link"]'
        )
        
        for i, element in enumerate(interactive_elements):
            # Check if element is focusable
            is_focusable = await element.evaluate('el => el.tabIndex >= 0 || el.matches("a, button, input, select, textarea")')
            
            if is_focusable:
                # Check if element has visible focus indicator
                await element.focus()
                
                # Get computed styles for focus state
                focus_styles = await element.evaluate('''
                    el => {
                        const styles = window.getComputedStyle(el, ':focus');
                        return {
                            outline: styles.outline,
                            outlineWidth: styles.outlineWidth,
                            outlineStyle: styles.outlineStyle,
                            outlineColor: styles.outlineColor,
                            boxShadow: styles.boxShadow
                        };
                    }
                ''')
                
                # Check if there's a visible focus indicator
                has_focus_indicator = (
                    focus_styles['outline'] != 'none' or
                    focus_styles['outlineWidth'] != '0px' or
                    focus_styles['boxShadow'] != 'none'
                )
                
                if not has_focus_indicator:
                    element_info = await element.evaluate('''
                        el => ({
                            tagName: el.tagName,
                            id: el.id,
                            className: el.className,
                            textContent: el.textContent?.substring(0, 50)
                        })
                    ''')
                    
                    issues.append({
                        'type': 'missing_focus_indicator',
                        'element': element_info,
                        'message': 'Interactive element lacks visible focus indicator'
                    })
        
        return issues
    
    async def check_aria_labels(self) -> List[Dict[str, Any]]:
        """Check ARIA labels and accessibility attributes."""
        issues = []
        
        # Check for missing alt text on images
        images = await self.page.query_selector_all('img')
        for img in images:
            alt_text = await img.get_attribute('alt')
            src = await img.get_attribute('src')
            
            if alt_text is None and src and not src.startswith('data:'):
                issues.append({
                    'type': 'missing_alt_text',
                    'element': {'tagName': 'IMG', 'src': src},
                    'message': 'Image missing alt text'
                })
        
        # Check for form labels
        form_inputs = await self.page.query_selector_all('input[type="text"], input[type="email"], input[type="password"], textarea, select')
        for input_elem in form_inputs:
            input_id = await input_elem.get_attribute('id')
            aria_label = await input_elem.get_attribute('aria-label')
            aria_labelledby = await input_elem.get_attribute('aria-labelledby')
            
            # Check if there's an associated label
            has_label = False
            if input_id:
                label = await self.page.query_selector(f'label[for="{input_id}"]')
                has_label = label is not None
            
            if not has_label and not aria_label and not aria_labelledby:
                input_info = await input_elem.evaluate('''
                    el => ({
                        tagName: el.tagName,
                        type: el.type,
                        id: el.id,
                        name: el.name
                    })
                ''')
                
                issues.append({
                    'type': 'missing_form_label',
                    'element': input_info,
                    'message': 'Form input missing accessible label'
                })
        
        # Check for proper heading hierarchy
        headings = await self.page.query_selector_all('h1, h2, h3, h4, h5, h6')
        heading_levels = []
        
        for heading in headings:
            tag_name = await heading.evaluate('el => el.tagName')
            level = int(tag_name[1])
            heading_levels.append(level)
        
        # Check for skipped heading levels
        for i in range(1, len(heading_levels)):
            current_level = heading_levels[i]
            previous_level = heading_levels[i-1]
            
            if current_level > previous_level + 1:
                issues.append({
                    'type': 'skipped_heading_level',
                    'message': f'Heading level skipped: h{previous_level} to h{current_level}'
                })
        
        return issues
    
    async def check_color_contrast(self) -> List[Dict[str, Any]]:
        """Check color contrast compliance."""
        issues = []
        
        # Get all text elements
        text_elements = await self.page.query_selector_all('p, span, div, h1, h2, h3, h4, h5, h6, a, button, label')
        
        for element in text_elements:
            # Get computed styles
            styles = await element.evaluate('''
                el => {
                    const computed = window.getComputedStyle(el);
                    return {
                        color: computed.color,
                        backgroundColor: computed.backgroundColor,
                        fontSize: computed.fontSize,
                        fontWeight: computed.fontWeight
                    };
                }
            ''')
            
            # Skip if no text content
            text_content = await element.text_content()
            if not text_content or not text_content.strip():
                continue
            
            # Parse colors (simplified - in real implementation would handle all color formats)
            color_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', styles['color'])
            bg_color_match = re.search(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', styles['backgroundColor'])
            
            if color_match and bg_color_match:
                # Convert RGB to hex for contrast calculation
                text_color = '#{:02x}{:02x}{:02x}'.format(*map(int, color_match.groups()))
                bg_color = '#{:02x}{:02x}{:02x}'.format(*map(int, bg_color_match.groups()))
                
                # Calculate contrast ratio
                contrast_ratio = ColorContrastAnalyzer.calculate_contrast_ratio(text_color, bg_color)
                
                # Determine if text is large (18pt+ or 14pt+ bold)
                font_size = float(styles['fontSize'].replace('px', ''))
                font_weight = styles['fontWeight']
                is_large_text = font_size >= 18 or (font_size >= 14 and font_weight in ['bold', '700', '800', '900'])
                
                # Check WCAG compliance
                meets_aa = ColorContrastAnalyzer.meets_wcag_aa(contrast_ratio, is_large_text)
                
                if not meets_aa:
                    element_info = await element.evaluate('''
                        el => ({
                            tagName: el.tagName,
                            id: el.id,
                            className: el.className,
                            textContent: el.textContent?.substring(0, 50)
                        })
                    ''')
                    
                    issues.append({
                        'type': 'insufficient_color_contrast',
                        'element': element_info,
                        'contrast_ratio': round(contrast_ratio, 2),
                        'required_ratio': 3.0 if is_large_text else 4.5,
                        'text_color': text_color,
                        'background_color': bg_color,
                        'message': f'Insufficient color contrast: {contrast_ratio:.2f}'
                    })
        
        return issues
    
    async def check_semantic_markup(self) -> List[Dict[str, Any]]:
        """Check semantic HTML markup."""
        issues = []
        
        # Check for proper landmark usage
        landmarks = await self.page.query_selector_all('[role="main"], [role="navigation"], [role="banner"], [role="contentinfo"], main, nav, header, footer')
        
        if len(landmarks) == 0:
            issues.append({
                'type': 'missing_landmarks',
                'message': 'Page lacks semantic landmarks (main, nav, header, footer)'
            })
        
        # Check for proper list markup
        list_items = await self.page.query_selector_all('li')
        for li in list_items:
            parent = await li.evaluate('el => el.parentElement')
            parent_tag = await li.evaluate('el => el.parentElement?.tagName')
            
            if parent_tag not in ['UL', 'OL']:
                issues.append({
                    'type': 'improper_list_markup',
                    'message': 'List item (li) not contained within ul or ol'
                })
        
        # Check for proper table markup
        tables = await self.page.query_selector_all('table')
        for table in tables:
            # Check for table headers
            headers = await table.query_selector_all('th')
            if len(headers) == 0:
                issues.append({
                    'type': 'table_missing_headers',
                    'message': 'Data table missing header cells (th)'
                })
            
            # Check for table caption
            caption = await table.query_selector('caption')
            if not caption:
                issues.append({
                    'type': 'table_missing_caption',
                    'message': 'Data table missing caption'
                })
        
        return issues


class TestWCAGCompliance:
    """WCAG compliance tests."""
    
    @pytest.fixture
    async def accessibility_page(self):
        """Setup page for accessibility testing."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            yield page
            
            await context.close()
            await browser.close()
    
    @pytest.mark.accessibility
    async def test_homepage_accessibility(self, accessibility_page):
        """Test homepage accessibility compliance."""
        page = accessibility_page
        tester = AccessibilityTester(page)
        
        # Navigate to homepage
        await page.goto("http://localhost:3000")
        await page.wait_for_load_state("networkidle")
        
        # Run comprehensive accessibility analysis
        axe_results = await tester.run_axe_analysis()
        keyboard_issues = await tester.check_keyboard_navigation()
        aria_issues = await tester.check_aria_labels()
        contrast_issues = await tester.check_color_contrast()
        semantic_issues = await tester.check_semantic_markup()
        
        # Collect all issues
        all_issues = (
            keyboard_issues + 
            aria_issues + 
            contrast_issues + 
            semantic_issues
        )
        
        # Log issues for review
        if all_issues:
            logger.warning(f"Found {len(all_issues)} accessibility issues on homepage:")
            for issue in all_issues:
                logger.warning(f"- {issue['type']}: {issue['message']}")
        
        # Assert no critical accessibility violations
        critical_issues = [issue for issue in all_issues if issue['type'] in [
            'missing_alt_text', 'missing_form_label', 'insufficient_color_contrast'
        ]]
        
        assert len(critical_issues) == 0, f"Critical accessibility issues found: {critical_issues}"
    
    @pytest.mark.accessibility
    async def test_form_accessibility(self, accessibility_page):
        """Test form accessibility compliance."""
        page = accessibility_page
        tester = AccessibilityTester(page)
        
        # Navigate to report form
        await page.goto("http://localhost:3000/report")
        await page.wait_for_load_state("networkidle")
        
        # Check form-specific accessibility
        aria_issues = await tester.check_aria_labels()
        keyboard_issues = await tester.check_keyboard_navigation()
        
        # Test form navigation with keyboard
        await page.press('body', 'Tab')  # Focus first element
        
        # Get all form inputs
        form_inputs = await page.query_selector_all('input, textarea, select, button')
        
        for i, input_elem in enumerate(form_inputs):
            # Check if element can receive focus
            await input_elem.focus()
            focused_element = await page.evaluate('document.activeElement.tagName')
            
            # Verify element is focusable
            assert focused_element in ['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON'], \
                f"Form element {i} is not properly focusable"
        
        # Check for form validation accessibility
        submit_button = await page.query_selector('[type="submit"], button[type="submit"]')
        if submit_button:
            await submit_button.click()
            
            # Check if validation errors are announced
            error_messages = await page.query_selector_all('[role="alert"], .error-message, .validation-error')
            
            for error in error_messages:
                # Verify error messages are associated with form fields
                aria_describedby = await error.get_attribute('aria-describedby')
                aria_live = await error.get_attribute('aria-live')
                
                # Error messages should be announced to screen readers
                assert aria_live in ['polite', 'assertive'] or aria_describedby, \
                    "Error messages should be properly announced to screen readers"
    
    @pytest.mark.accessibility
    async def test_dashboard_accessibility(self, accessibility_page):
        """Test dashboard accessibility compliance."""
        page = accessibility_page
        tester = AccessibilityTester(page)
        
        # Navigate to dashboard
        await page.goto("http://localhost:3000/dashboard")
        await page.wait_for_load_state("networkidle")
        
        # Check data visualization accessibility
        charts = await page.query_selector_all('[data-testid*="chart"], .chart, canvas')
        
        for chart in charts:
            # Check for alternative text or data table
            alt_text = await chart.get_attribute('alt')
            aria_label = await chart.get_attribute('aria-label')
            aria_describedby = await chart.get_attribute('aria-describedby')
            
            has_accessible_description = alt_text or aria_label or aria_describedby
            
            assert has_accessible_description, \
                "Charts and data visualizations must have accessible descriptions"
        
        # Check for data table alternatives
        data_tables = await page.query_selector_all('table')
        for table in data_tables:
            # Verify table has proper headers
            headers = await table.query_selector_all('th')
            assert len(headers) > 0, "Data tables must have header cells"
            
            # Check for table caption or summary
            caption = await table.query_selector('caption')
            summary = await table.get_attribute('summary')
            
            assert caption or summary, "Data tables should have captions or summaries"
    
    @pytest.mark.accessibility
    async def test_mobile_accessibility(self, accessibility_page):
        """Test mobile accessibility compliance."""
        page = accessibility_page
        
        # Set mobile viewport
        await page.set_viewport_size({"width": 375, "height": 667})
        
        # Navigate to homepage
        await page.goto("http://localhost:3000")
        await page.wait_for_load_state("networkidle")
        
        # Check touch target sizes
        interactive_elements = await page.query_selector_all('button, a, input, [role="button"]')
        
        for element in interactive_elements:
            bounding_box = await element.bounding_box()
            
            if bounding_box:
                # WCAG recommends minimum 44x44 CSS pixels for touch targets
                min_size = 44
                
                assert bounding_box['width'] >= min_size or bounding_box['height'] >= min_size, \
                    f"Touch target too small: {bounding_box['width']}x{bounding_box['height']} (minimum {min_size}x{min_size})"
        
        # Test mobile navigation
        mobile_menu_button = await page.query_selector('[data-testid="mobile-menu-button"], .mobile-menu-toggle')
        
        if mobile_menu_button:
            # Check if mobile menu button is accessible
            aria_label = await mobile_menu_button.get_attribute('aria-label')
            aria_expanded = await mobile_menu_button.get_attribute('aria-expanded')
            
            assert aria_label, "Mobile menu button should have aria-label"
            assert aria_expanded is not None, "Mobile menu button should have aria-expanded attribute"
            
            # Test menu toggle functionality
            await mobile_menu_button.click()
            
            # Check if menu state is properly announced
            aria_expanded_after = await mobile_menu_button.get_attribute('aria-expanded')
            assert aria_expanded != aria_expanded_after, "Mobile menu aria-expanded should toggle"


# Accessibility test utilities
@pytest.fixture
def wcag_standards():
    """WCAG standards and requirements."""
    return {
        "color_contrast": {
            "aa_normal": 4.5,
            "aa_large": 3.0,
            "aaa_normal": 7.0,
            "aaa_large": 4.5
        },
        "touch_targets": {
            "minimum_size": 44  # CSS pixels
        },
        "timing": {
            "no_time_limits": True,
            "adjustable_timing": True
        }
    }


@pytest.fixture
def accessibility_test_config():
    """Accessibility testing configuration."""
    return {
        "standards": ["WCAG2A", "WCAG2AA"],
        "test_levels": ["A", "AA"],
        "ignore_rules": [],
        "custom_rules": {
            "color_contrast_enhanced": True,
            "keyboard_navigation_complete": True,
            "screen_reader_compatibility": True
        }
    }
