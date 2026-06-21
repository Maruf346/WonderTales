import { Route, Routes } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import LandingPage from './pages/LandingPage'
import BlogsPage from './pages/BlogsPage'
import BlogDetailPage from './pages/BlogDetailPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<LandingPage />} />
        <Route path="blogs" element={<BlogsPage />} />
        <Route path="blog/:slug" element={<BlogDetailPage />} />
      </Route>
    </Routes>
  )
}

export default App