import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import React from 'react';
import AegisLanding from './App';

describe('AegisLanding', () => {
  it('renders landing navigation', () => {
    render(<AegisLanding />);
    expect(screen.getByText(/AEGIS-AI/i)).toBeInTheDocument();
    expect(screen.getByText(/AGENCY LOGIN/i)).toBeInTheDocument();
  });
});
