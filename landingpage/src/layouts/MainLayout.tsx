import { Outlet } from 'react-router-dom'
import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import MagicCursor from '../components/MagicCursor'

export default function MainLayout() {
  return (
    <div className="min-h-screen bg-navy-950 text-slate-200">
      <MagicCursor />
      <Navbar />
      <main>
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
