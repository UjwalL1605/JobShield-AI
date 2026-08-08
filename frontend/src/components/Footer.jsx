import { Shield, ExternalLink, Heart } from 'lucide-react'
import { Link } from 'react-router-dom'
import './Footer.css'

function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div className="footer-brand">
            <Link to="/" className="footer-logo">
              <div className="footer-logo-icon">
                <Shield size={20} />
              </div>
              <span>Job<span className="text-gradient">Shield</span> AI</span>
            </Link>
            <p className="footer-desc">
              AI-powered protection against fake job and internship scams.
              Stay safe, stay informed.
            </p>
          </div>

          <div className="footer-links-group">
            <h4 className="footer-heading">Platform</h4>
            <Link to="/analyze" className="footer-link">Analyze Message</Link>
            <Link to="/report" className="footer-link">Report Scam</Link>
            <Link to="/about" className="footer-link">How It Works</Link>
          </div>

          <div className="footer-links-group">
            <h4 className="footer-heading">Resources</h4>
            <a href="https://cybercrime.gov.in" target="_blank" rel="noopener noreferrer" className="footer-link">
              Cyber Crime Portal
            </a>
            <a href="https://consumerhelpline.gov.in" target="_blank" rel="noopener noreferrer" className="footer-link">
              Consumer Helpline
            </a>
          </div>
        </div>

        <div className="footer-bottom">
          <p className="footer-copyright">
            © {new Date().getFullYear()} JobShield AI. Built with <Heart size={14} className="footer-heart" /> for student safety.
          </p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
