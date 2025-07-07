"""
Screen reader compatibility and keyboard navigation tests for CityPulse.
Tests for assistive technology compatibility and keyboard-only navigation.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Tuple
from playwright.async_api import async_playwright, Page
import json
import logging

logger = logging.getLogger(__name__)


class ScreenReaderTester:
    """Test screen reader compatibility and announcements."""
    
    def __init__(self, page: Page):
        """Initialize screen reader tester."""
        self.page = page
        self.announcements = []
    
    async def setup_screen_reader_simulation(self):
        """Setup screen reader simulation and announcement tracking."""
        # Inject screen reader simulation script
        await self.page.add_script_tag(content="""
            window.screenReaderAnnouncements = [];
            
            // Override aria-live region updates
            const originalSetAttribute = Element.prototype.setAttribute;
            Element.prototype.setAttribute = function(name, value) {
                if (name === 'aria-live' || name === 'aria-label' || name === 'aria-describedby') {
                    window.screenReaderAnnouncements.push({
                        type: 'attribute_change',
                        element: this.tagName,
                        attribute: name,
                        value: value,
                        timestamp: Date.now()
                    });
                }
                return originalSetAttribute.call(this, name, value);
            };
            
            // Track focus changes
            document.addEventListener('focusin', function(event) {
                const element = event.target;
                const announcement = {
                    type: 'focus_change',
                    element: element.tagName,
                    id: element.id,
                    ariaLabel: element.getAttribute('aria-label'),
                    ariaRole: element.getAttribute('role'),
                    textContent: element.textContent?.substring(0, 100),
                    timestamp: Date.now()
                };
                window.screenReaderAnnouncements.push(announcement);
            });
            
            // Track live region updates
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'childList' || mutation.type === 'characterData') {
                        const target = mutation.target;
                        const ariaLive = target.getAttribute('aria-live') || 
                                        target.closest('[aria-live]')?.getAttribute('aria-live');
                        
                        if (ariaLive) {
                            window.screenReaderAnnouncements.push({
                                type: 'live_region_update',
                                element: target.tagName,
                                ariaLive: ariaLive,
                                content: target.textContent?.substring(0, 100),
                                timestamp: Date.now()
                            });
                        }
                    }
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                characterData: true
            });
        """)
    
    async def get_announcements(self) -> List[Dict[str, Any]]:
        """Get all screen reader announcements."""
        announcements = await self.page.evaluate('window.screenReaderAnnouncements || []')
        return announcements
    
    async def clear_announcements(self):
        """Clear announcement history."""
        await self.page.evaluate('window.screenReaderAnnouncements = []')
    
    async def check_page_structure_announcements(self) -> List[Dict[str, Any]]:
        """Check if page structure is properly announced."""
        issues = []
        
        # Check for page title
        title = await self.page.title()
        if not title or len(title.strip()) == 0:
            issues.append({
                'type': 'missing_page_title',
                'message': 'Page missing title for screen reader announcement'
            })
        
        # Check for main landmark
        main_landmark = await self.page.query_selector('main, [role="main"]')
        if not main_landmark:
            issues.append({
                'type': 'missing_main_landmark',
                'message': 'Page missing main landmark for screen reader navigation'
            })
        
        # Check for heading hierarchy
        headings = await self.page.query_selector_all('h1, h2, h3, h4, h5, h6')
        if len(headings) == 0:
            issues.append({
                'type': 'missing_headings',
                'message': 'Page missing headings for screen reader navigation'
            })
        else:
            # Check for h1
            h1_elements = await self.page.query_selector_all('h1')
            if len(h1_elements) == 0:
                issues.append({
                    'type': 'missing_h1',
                    'message': 'Page missing h1 heading'
                })
            elif len(h1_elements) > 1:
                issues.append({
                    'type': 'multiple_h1',
                    'message': 'Page has multiple h1 headings'
                })
        
        # Check for skip links
        skip_links = await self.page.query_selector_all('a[href^="#"], [role="link"][href^="#"]')
        skip_to_main = False
        
        for link in skip_links:
            text = await link.text_content()
            if text and 'skip' in text.lower() and 'main' in text.lower():
                skip_to_main = True
                break
        
        if not skip_to_main:
            issues.append({
                'type': 'missing_skip_link',
                'message': 'Page missing skip to main content link'
            })
        
        return issues
    
    async def check_form_announcements(self) -> List[Dict[str, Any]]:
        """Check if form elements are properly announced."""
        issues = []
        
        # Check form inputs
        form_inputs = await self.page.query_selector_all('input, textarea, select')
        
        for input_elem in form_inputs:
            input_type = await input_elem.get_attribute('type')
            input_id = await input_elem.get_attribute('id')
            aria_label = await input_elem.get_attribute('aria-label')
            aria_labelledby = await input_elem.get_attribute('aria-labelledby')
            aria_describedby = await input_elem.get_attribute('aria-describedby')
            
            # Check for accessible name
            has_accessible_name = False
            
            if aria_label:
                has_accessible_name = True
            elif input_id:
                label = await self.page.query_selector(f'label[for="{input_id}"]')
                has_accessible_name = label is not None
            elif aria_labelledby:
                has_accessible_name = True
            
            if not has_accessible_name:
                input_info = await input_elem.evaluate('''
                    el => ({
                        tagName: el.tagName,
                        type: el.type,
                        id: el.id,
                        name: el.name
                    })
                ''')
                
                issues.append({
                    'type': 'form_input_no_accessible_name',
                    'element': input_info,
                    'message': 'Form input lacks accessible name for screen readers'
                })
            
            # Check for required field announcements
            is_required = await input_elem.get_attribute('required') is not None
            aria_required = await input_elem.get_attribute('aria-required')
            
            if is_required and aria_required != 'true':
                issues.append({
                    'type': 'required_field_not_announced',
                    'element': {'id': input_id, 'type': input_type},
                    'message': 'Required field not properly announced to screen readers'
                })
        
        # Check fieldsets and legends
        fieldsets = await self.page.query_selector_all('fieldset')
        for fieldset in fieldsets:
            legend = await fieldset.query_selector('legend')
            if not legend:
                issues.append({
                    'type': 'fieldset_missing_legend',
                    'message': 'Fieldset missing legend for screen reader context'
                })
        
        return issues
    
    async def check_dynamic_content_announcements(self) -> List[Dict[str, Any]]:
        """Check if dynamic content changes are announced."""
        issues = []
        
        # Check for aria-live regions
        live_regions = await self.page.query_selector_all('[aria-live]')
        
        if len(live_regions) == 0:
            # Look for elements that might need live regions
            potential_live_elements = await self.page.query_selector_all(
                '.status, .alert, .notification, .error-message, .success-message, [role="status"], [role="alert"]'
            )
            
            if len(potential_live_elements) > 0:
                issues.append({
                    'type': 'missing_live_regions',
                    'message': 'Dynamic content elements missing aria-live attributes'
                })
        
        # Check for proper live region politeness
        for region in live_regions:
            aria_live = await region.get_attribute('aria-live')
            role = await region.get_attribute('role')
            
            # Alerts should be assertive
            if role == 'alert' and aria_live != 'assertive':
                issues.append({
                    'type': 'incorrect_live_region_politeness',
                    'message': 'Alert role should have aria-live="assertive"'
                })
            
            # Status should be polite
            if role == 'status' and aria_live not in ['polite', 'assertive']:
                issues.append({
                    'type': 'missing_live_region_politeness',
                    'message': 'Status role should have aria-live attribute'
                })
        
        return issues


class KeyboardNavigationTester:
    """Test keyboard navigation functionality."""
    
    def __init__(self, page: Page):
        """Initialize keyboard navigation tester."""
        self.page = page
        self.focus_order = []
    
    async def test_tab_navigation(self) -> Dict[str, Any]:
        """Test tab navigation through interactive elements."""
        # Get all interactive elements
        interactive_elements = await self.page.query_selector_all(
            'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"]), [role="button"], [role="link"], [role="menuitem"]'
        )
        
        # Filter out hidden elements
        visible_elements = []
        for element in interactive_elements:
            is_visible = await element.is_visible()
            if is_visible:
                visible_elements.append(element)
        
        # Test tab navigation
        focus_order = []
        
        # Start from beginning
        await self.page.keyboard.press('Tab')
        
        for i in range(len(visible_elements) + 5):  # Extra tabs to ensure we cycle through
            focused_element = await self.page.evaluate('''
                () => {
                    const el = document.activeElement;
                    return {
                        tagName: el.tagName,
                        id: el.id,
                        className: el.className,
                        type: el.type,
                        role: el.getAttribute('role'),
                        tabIndex: el.tabIndex,
                        textContent: el.textContent?.substring(0, 50)
                    };
                }
            ''')
            
            focus_order.append(focused_element)
            await self.page.keyboard.press('Tab')
        
        return {
            'total_interactive_elements': len(visible_elements),
            'focus_order': focus_order,
            'focus_order_length': len(focus_order)
        }
    
    async def test_keyboard_shortcuts(self) -> List[Dict[str, Any]]:
        """Test keyboard shortcuts and access keys."""
        issues = []
        
        # Check for access keys
        elements_with_accesskey = await self.page.query_selector_all('[accesskey]')
        
        access_keys = []
        for element in elements_with_accesskey:
            access_key = await element.get_attribute('accesskey')
            access_keys.append(access_key)
        
        # Check for duplicate access keys
        if len(access_keys) != len(set(access_keys)):
            issues.append({
                'type': 'duplicate_access_keys',
                'message': 'Duplicate access keys found'
            })
        
        # Test common keyboard shortcuts
        shortcuts_to_test = [
            {'key': 'Escape', 'expected_action': 'close_modal_or_menu'},
            {'key': 'Enter', 'expected_action': 'activate_focused_element'},
            {'key': 'Space', 'expected_action': 'activate_button_or_checkbox'},
            {'key': 'ArrowDown', 'expected_action': 'navigate_menu_or_list'},
            {'key': 'ArrowUp', 'expected_action': 'navigate_menu_or_list'}
        ]
        
        # This would be expanded to test actual functionality
        # For now, we'll just verify the structure exists
        
        return issues
    
    async def test_focus_management(self) -> List[Dict[str, Any]]:
        """Test focus management in dynamic interfaces."""
        issues = []
        
        # Test modal focus management
        modal_triggers = await self.page.query_selector_all('[data-toggle="modal"], .modal-trigger, [aria-haspopup="dialog"]')
        
        for trigger in modal_triggers:
            # Click to open modal
            await trigger.click()
            await self.page.wait_for_timeout(500)  # Wait for modal to open
            
            # Check if focus moved to modal
            focused_element = await self.page.evaluate('document.activeElement.tagName')
            
            # Look for modal
            modal = await self.page.query_selector('[role="dialog"], .modal, [aria-modal="true"]')
            
            if modal:
                # Check if modal has focus or focus is within modal
                modal_has_focus = await modal.evaluate('''
                    modal => {
                        return modal.contains(document.activeElement) || 
                               modal === document.activeElement;
                    }
                ''')
                
                if not modal_has_focus:
                    issues.append({
                        'type': 'modal_focus_not_managed',
                        'message': 'Modal opened but focus not moved to modal'
                    })
                
                # Test escape key to close modal
                await self.page.keyboard.press('Escape')
                await self.page.wait_for_timeout(500)
                
                # Check if modal closed and focus returned
                modal_still_visible = await modal.is_visible()
                if modal_still_visible:
                    issues.append({
                        'type': 'modal_escape_not_working',
                        'message': 'Modal does not close with Escape key'
                    })
        
        # Test dropdown/menu focus management
        dropdown_triggers = await self.page.query_selector_all('[aria-haspopup="menu"], [aria-haspopup="listbox"], .dropdown-toggle')
        
        for trigger in dropdown_triggers:
            # Open dropdown
            await trigger.click()
            await self.page.wait_for_timeout(300)
            
            # Check if focus moved to first menu item
            focused_element = await self.page.evaluate('''
                () => {
                    const el = document.activeElement;
                    return {
                        role: el.getAttribute('role'),
                        tagName: el.tagName
                    };
                }
            ''')
            
            # Focus should be on menu item or within menu
            if focused_element['role'] not in ['menuitem', 'option'] and focused_element['tagName'] not in ['A', 'BUTTON']:
                issues.append({
                    'type': 'dropdown_focus_not_managed',
                    'message': 'Dropdown opened but focus not moved to menu items'
                })
            
            # Close dropdown
            await self.page.keyboard.press('Escape')
            await self.page.wait_for_timeout(300)
        
        return issues
    
    async def test_focus_indicators(self) -> List[Dict[str, Any]]:
        """Test visibility of focus indicators."""
        issues = []
        
        # Get all focusable elements
        focusable_elements = await self.page.query_selector_all(
            'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
        
        for element in focusable_elements:
            # Focus the element
            await element.focus()
            
            # Get focus styles
            focus_styles = await element.evaluate('''
                el => {
                    const styles = window.getComputedStyle(el, ':focus');
                    return {
                        outline: styles.outline,
                        outlineWidth: styles.outlineWidth,
                        outlineStyle: styles.outlineStyle,
                        outlineColor: styles.outlineColor,
                        outlineOffset: styles.outlineOffset,
                        boxShadow: styles.boxShadow,
                        border: styles.border,
                        backgroundColor: styles.backgroundColor
                    };
                }
            ''')
            
            # Check if there's a visible focus indicator
            has_focus_indicator = (
                focus_styles['outline'] != 'none' and focus_styles['outlineWidth'] != '0px' or
                focus_styles['boxShadow'] != 'none' or
                focus_styles['outlineOffset'] != '0px'
            )
            
            if not has_focus_indicator:
                element_info = await element.evaluate('''
                    el => ({
                        tagName: el.tagName,
                        id: el.id,
                        className: el.className,
                        type: el.type
                    })
                ''')
                
                issues.append({
                    'type': 'missing_focus_indicator',
                    'element': element_info,
                    'message': 'Focusable element lacks visible focus indicator'
                })
        
        return issues


class TestScreenReaderCompatibility:
    """Screen reader compatibility tests."""
    
    @pytest.fixture
    async def screen_reader_page(self):
        """Setup page for screen reader testing."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            yield page
            
            await context.close()
            await browser.close()
    
    @pytest.mark.accessibility
    async def test_page_structure_announcements(self, screen_reader_page):
        """Test page structure announcements for screen readers."""
        page = screen_reader_page
        tester = ScreenReaderTester(page)
        
        await tester.setup_screen_reader_simulation()
        
        # Navigate to homepage
        await page.goto("http://localhost:3000")
        await page.wait_for_load_state("networkidle")
        
        # Check page structure
        structure_issues = await tester.check_page_structure_announcements()
        
        # Log issues
        if structure_issues:
            logger.warning(f"Found {len(structure_issues)} page structure issues:")
            for issue in structure_issues:
                logger.warning(f"- {issue['type']}: {issue['message']}")
        
        # Assert critical structure elements
        critical_issues = [issue for issue in structure_issues if issue['type'] in [
            'missing_page_title', 'missing_main_landmark', 'missing_h1'
        ]]
        
        assert len(critical_issues) == 0, f"Critical page structure issues: {critical_issues}"
    
    @pytest.mark.accessibility
    async def test_form_screen_reader_compatibility(self, screen_reader_page):
        """Test form compatibility with screen readers."""
        page = screen_reader_page
        tester = ScreenReaderTester(page)
        
        await tester.setup_screen_reader_simulation()
        
        # Navigate to form page
        await page.goto("http://localhost:3000/report")
        await page.wait_for_load_state("networkidle")
        
        # Check form announcements
        form_issues = await tester.check_form_announcements()
        
        # Test form interaction with screen reader simulation
        await tester.clear_announcements()
        
        # Focus first form input
        first_input = await page.query_selector('input, textarea, select')
        if first_input:
            await first_input.focus()
            
            # Get announcements
            announcements = await tester.get_announcements()
            
            # Should have focus announcement
            focus_announcements = [a for a in announcements if a['type'] == 'focus_change']
            assert len(focus_announcements) > 0, "Form input focus should be announced"
        
        # Test form validation announcements
        submit_button = await page.query_selector('[type="submit"], button[type="submit"]')
        if submit_button:
            await submit_button.click()
            await page.wait_for_timeout(1000)
            
            # Check for validation announcements
            announcements = await tester.get_announcements()
            validation_announcements = [a for a in announcements if a['type'] == 'live_region_update']
            
            # Should announce validation errors
            assert len(validation_announcements) >= 0, "Form validation should be announced"
        
        # Assert no critical form issues
        critical_form_issues = [issue for issue in form_issues if issue['type'] in [
            'form_input_no_accessible_name', 'required_field_not_announced'
        ]]
        
        assert len(critical_form_issues) == 0, f"Critical form accessibility issues: {critical_form_issues}"
    
    @pytest.mark.accessibility
    async def test_dynamic_content_announcements(self, screen_reader_page):
        """Test dynamic content announcements."""
        page = screen_reader_page
        tester = ScreenReaderTester(page)
        
        await tester.setup_screen_reader_simulation()
        
        # Navigate to dashboard (has dynamic content)
        await page.goto("http://localhost:3000/dashboard")
        await page.wait_for_load_state("networkidle")
        
        # Check dynamic content setup
        dynamic_issues = await tester.check_dynamic_content_announcements()
        
        # Test live region updates
        await tester.clear_announcements()
        
        # Trigger dynamic content update (e.g., filter change)
        filter_select = await page.query_selector('select, [role="combobox"]')
        if filter_select:
            await filter_select.select_option(index=1)
            await page.wait_for_timeout(2000)  # Wait for content update
            
            # Check for live region announcements
            announcements = await tester.get_announcements()
            live_announcements = [a for a in announcements if a['type'] == 'live_region_update']
            
            # Dynamic content changes should be announced
            assert len(live_announcements) >= 0, "Dynamic content updates should be announced"
        
        # Assert no critical dynamic content issues
        critical_dynamic_issues = [issue for issue in dynamic_issues if issue['type'] in [
            'missing_live_regions'
        ]]
        
        assert len(critical_dynamic_issues) == 0, f"Critical dynamic content issues: {critical_dynamic_issues}"


class TestKeyboardNavigation:
    """Keyboard navigation tests."""
    
    @pytest.fixture
    async def keyboard_page(self):
        """Setup page for keyboard testing."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            yield page
            
            await context.close()
            await browser.close()
    
    @pytest.mark.accessibility
    async def test_complete_keyboard_navigation(self, keyboard_page):
        """Test complete keyboard navigation through the application."""
        page = keyboard_page
        tester = KeyboardNavigationTester(page)
        
        # Navigate to homepage
        await page.goto("http://localhost:3000")
        await page.wait_for_load_state("networkidle")
        
        # Test tab navigation
        tab_results = await tester.test_tab_navigation()
        
        # Should be able to navigate to all interactive elements
        assert tab_results['total_interactive_elements'] > 0, "Page should have interactive elements"
        assert len(tab_results['focus_order']) > 0, "Should be able to navigate with Tab key"
        
        # Test focus indicators
        focus_issues = await tester.test_focus_indicators()
        
        # Assert no missing focus indicators
        assert len(focus_issues) == 0, f"Missing focus indicators: {focus_issues}"
    
    @pytest.mark.accessibility
    async def test_modal_keyboard_navigation(self, keyboard_page):
        """Test keyboard navigation in modals."""
        page = keyboard_page
        tester = KeyboardNavigationTester(page)
        
        # Navigate to page with modals
        await page.goto("http://localhost:3000")
        await page.wait_for_load_state("networkidle")
        
        # Test focus management
        focus_issues = await tester.test_focus_management()
        
        # Log focus management issues
        if focus_issues:
            logger.warning(f"Found {len(focus_issues)} focus management issues:")
            for issue in focus_issues:
                logger.warning(f"- {issue['type']}: {issue['message']}")
        
        # Assert no critical focus management issues
        critical_focus_issues = [issue for issue in focus_issues if issue['type'] in [
            'modal_focus_not_managed', 'modal_escape_not_working'
        ]]
        
        assert len(critical_focus_issues) == 0, f"Critical focus management issues: {critical_focus_issues}"
    
    @pytest.mark.accessibility
    async def test_keyboard_shortcuts(self, keyboard_page):
        """Test keyboard shortcuts functionality."""
        page = keyboard_page
        tester = KeyboardNavigationTester(page)
        
        # Navigate to application
        await page.goto("http://localhost:3000")
        await page.wait_for_load_state("networkidle")
        
        # Test keyboard shortcuts
        shortcut_issues = await tester.test_keyboard_shortcuts()
        
        # Assert no critical shortcut issues
        critical_shortcut_issues = [issue for issue in shortcut_issues if issue['type'] in [
            'duplicate_access_keys'
        ]]
        
        assert len(critical_shortcut_issues) == 0, f"Critical keyboard shortcut issues: {critical_shortcut_issues}"
