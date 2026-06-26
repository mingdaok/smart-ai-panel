import { Outlet } from 'react-router-dom';
import './styles/tokens.css';

export default function App() {
  return (
    <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)]">
      <Outlet />
    </div>
  );
}
