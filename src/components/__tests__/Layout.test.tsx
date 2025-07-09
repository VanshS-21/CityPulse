/**
 * @jest-environment jsdom
 */
import { render, screen } from '@testing-library/react'
import Layout from '../common/Layout'

describe('Layout Component', () => {
  it('renders children correctly', () => {
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )
    
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('renders header and footer', () => {
    render(
      <Layout>
        <div>Test Content</div>
      </Layout>
    )
    
    // Check if header and footer are rendered
    // Note: These tests would need to be updated based on actual header/footer content
    expect(document.querySelector('header')).toBeInTheDocument()
    expect(document.querySelector('footer')).toBeInTheDocument()
  })
})
