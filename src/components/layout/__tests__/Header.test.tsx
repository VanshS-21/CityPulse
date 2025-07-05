import { render, screen } from '@testing-library/react';
import Header from '../Header';

describe('Header', () => {
  it('renders the header with navigation links', () => {
    render(<Header />);

    // Check for the brand name
    const brandLink = screen.getByRole('link', { name: /citypulse/i });
    expect(brandLink).toBeInTheDocument();
    expect(brandLink).toHaveAttribute('href', '/');

    // Check for navigation links
    const homeLink = screen.getByRole('link', { name: /home/i });
    expect(homeLink).toBeInTheDocument();
    expect(homeLink).toHaveAttribute('href', '/');

    const submitReportLink = screen.getByRole('link', { name: /submit report/i });
    expect(submitReportLink).toBeInTheDocument();
    expect(submitReportLink).toHaveAttribute('href', '/submit-report');
  });
});
