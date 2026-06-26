// frontend/src/App.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';
import App from './App';
import HomePage from './pages/HomePage';

describe('App', () => {
  it('renders child route via Outlet', () => {
    const router = createMemoryRouter(
      [
        {
          path: '/',
          element: <App />,
          children: [{ index: true, element: <HomePage /> }],
        },
      ],
      { initialEntries: ['/'] }
    );
    render(<RouterProvider router={router} />);
    // HomePage renders the app title
    expect(screen.getByText(/AI Panel Studio/i)).toBeDefined();
  });
});
