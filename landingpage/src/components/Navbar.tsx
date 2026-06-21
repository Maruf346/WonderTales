import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import logoIcon from '../assets/logo.svg'

const navItems = [
  { label: 'Features', href: '/#features' },
  { label: 'How It Works', href: '/#how-it-works' },
  { label: 'Voice', href: '/#voice' },
  { label: 'Pricing', href: '/#pricing' },
  { label: 'Blog', href: '/blogs', highlight: false },
]

export default function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <header className="absolute top-0 w-full z-50">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6 lg:px-8">
        <NavLink to="/" className="flex items-center gap-3">
          <img src={logoIcon} alt="" className="h-10 object-contain" />
          <span className="text-xl font-serif tracking-wide">
            <span className="text-gold">WonderTales</span> <span className="text-white">Hub</span>
          </span>
        </NavLink>

        <nav className="hidden items-center gap-10 md:flex ml-10">
          {navItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className={`text-[13px] font-normal transition-colors text-white hover:text-gold`}
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-4">
          <a
            href={window.location.hostname === 'localhost' ? 'http://localhost:8000/admin/' : 'https://api.wondertaleshub.com/admin/'}
            className="hidden md:block rounded-md border border-white/20 bg-transparent px-5 py-2.5 text-[13px] font-semibold text-slate-300 transition hover:bg-white/10 hover:text-white"
          >
            Admin Login
          </a>
          <a
            href="/#pricing"
            className="hidden sm:block rounded-md bg-gradient-to-r from-orange-300 via-orange-400 to-orange-500 px-6 py-2.5 text-[13px] font-semibold text-white transition hover:opacity-90"
          >
            Get Download link
          </a>
          <button 
            className="md:hidden p-1 text-white" 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
              {isMobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {isMobileMenuOpen && (
        <div className="md:hidden bg-navy-950/95 backdrop-blur-md absolute top-full left-0 w-full border-t border-white/10 px-6 py-4 flex flex-col shadow-2xl">
          {navItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="text-base font-medium text-white hover:text-gold block py-3 border-b border-white/5"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              {item.label}
            </a>
          ))}
          <a
            href="/#pricing"
            className="text-base font-medium text-orange-400 block py-3 border-b border-white/5"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            Get Download link
          </a>
          <a
            href={window.location.hostname === 'localhost' ? 'http://localhost:8000/admin/' : 'https://api.wondertaleshub.com/admin/'}
            className="text-base font-medium text-gold hover:text-white block py-3"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            Admin Login
          </a>
        </div>
      )}
    </header>
  )
}
