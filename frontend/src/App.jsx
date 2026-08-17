import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import ErrorBoundary from './components/ErrorBoundary'
import CyberCanvas3D from './components/CyberCanvas3D'
import ScrollToTop from './components/ScrollToTop'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import AnalyzePage from './pages/AnalyzePage'
import ReportPage from './pages/ReportPage'
import AboutPage from './pages/AboutPage'
import { healthCheck } from './api/client'

function App() {
  // Proactive background ping to wake up cloud backend (e.g. Render) on initial page load
  useEffect(() => {
    healthCheck().catch(() => {})
  }, [])
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <CyberCanvas3D />
        <Router>
          <ScrollToTop />
          <Navbar />
          <main className="page">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/analyze" element={<AnalyzePage />} />
              <Route path="/report" element={<ReportPage />} />
              <Route path="/about" element={<AboutPage />} />
            </Routes>
          </main>
          <Footer />
        </Router>
      </ThemeProvider>
    </ErrorBoundary>
  )
}

export default App
