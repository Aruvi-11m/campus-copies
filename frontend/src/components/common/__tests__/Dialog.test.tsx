import { render, screen } from '@testing-library/react';
import { Dialog } from '../Dialog';

describe('Dialog', () => {
  it('renders correctly when open', () => {
    render(
      <Dialog isOpen={true} onClose={() => {}} title="Test Dialog">
        <p>Dialog Content</p>
      </Dialog>
    );
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Test Dialog')).toBeInTheDocument();
    expect(screen.getByText('Dialog Content')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <Dialog isOpen={false} onClose={() => {}} title="Test Dialog">
        <p>Dialog Content</p>
      </Dialog>
    );
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });
});
