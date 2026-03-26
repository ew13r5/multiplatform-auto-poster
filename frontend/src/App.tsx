import { BrowserRouter, Routes, Route } from 'react-router-dom'
import AppLayout from './components/Layout/AppLayout'
import Dashboard from './pages/Dashboard'
import Queue from './pages/Queue'
import Schedule from './pages/Schedule'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import { ToastProvider } from './components/shared/Toast'
import './index.css'

function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/queue" element={<Queue />} />
          <Route path="/schedule" element={<Schedule />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </AppLayout>
      </ToastProvider>
    </BrowserRouter>
  )
}

export default App
