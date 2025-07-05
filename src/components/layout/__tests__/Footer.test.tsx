import React from 'react';
import { render, screen } from '@testing-library/react';
import Footer from '../Footer';

describe('Footer', () => {
  it('renders the footer with the current year', () => {
    render(<Footer />);

    const currentYear = new Date().getFullYear();
    const footerText = screen.getByText(`© ${currentYear} CityPulse. All rights reserved.`);
    expect(footerText).toBeInTheDocument();
  });
});
