import { createBrowserRouter } from 'react-router-dom';
import App from './App';
import HomePage from './pages/HomePage';
import LobbyPage from './pages/LobbyPage';
import StudioPage from './pages/StudioPage';
import SummaryPage from './pages/SummaryPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'room/:id/lobby', element: <LobbyPage /> },
      { path: 'room/:id/studio', element: <StudioPage /> },
      { path: 'room/:id/summary', element: <SummaryPage /> },
    ],
  },
]);
