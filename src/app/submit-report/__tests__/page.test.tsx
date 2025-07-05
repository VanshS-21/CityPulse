import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SubmitReportPage from '../page';
import { useFormState } from 'react-dom';

// Mock react-dom's useFormState hook
jest.mock('react-dom', () => ({
  ...jest.requireActual('react-dom'),
  useFormState: jest.fn(),
}));

describe('SubmitReportPage', () => {
  const mockFormAction = jest.fn();

  beforeEach(() => {
    // Reset mocks before each test
    (useFormState as jest.Mock).mockReturnValue([{ message: '' }, mockFormAction]);
    jest.clearAllMocks();
  });

  it('renders the submit report form correctly', () => {
    render(<SubmitReportPage />);

    // Check for the page heading
    expect(screen.getByRole('heading', { name: /submit a new report/i })).toBeInTheDocument();

    // Check for form fields
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/location/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/upload media/i)).toBeInTheDocument();

    // Check for the submit button
    expect(screen.getByRole('button', { name: /submit report/i })).toBeInTheDocument();
  });

  it('allows user to fill and submit the form', async () => {
    render(<SubmitReportPage />);

    // Simulate user input
    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'Broken Streetlight' },
    });
    fireEvent.change(screen.getByLabelText(/description/i), {
      target: { value: 'The streetlight on the corner of 5th and Elm is out.' },
    });
    fireEvent.change(screen.getByLabelText(/location/i), {
      target: { value: 'Corner of 5th and Elm' },
    });

    // Simulate form submission
    fireEvent.click(screen.getByRole('button', { name: /submit report/i }));

    // The form's action prop is the mockFormAction, so we check if it was called.
    await waitFor(() => {
      expect(mockFormAction).toHaveBeenCalledTimes(1);
    });
  });
});
