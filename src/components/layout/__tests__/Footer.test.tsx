import { render, screen } from '@testing-library/react';
import Footer from '../Footer';

describe('Footer', () => {
  it('renders the footer with the correct text', () => {
    render(<Footer />);

    const footerText = screen.getByText(/© \d{4} CityPulse\. All rights reserved\./i);
    expect(footerText).toBeInTheDocument();
  });
});
