import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App'
import Home from './views/Home'
import Browse from './views/Browse'
import BootcampDetail from './views/BootcampDetail'
import PathDetail from './views/PathDetail'
import CourseDetail from './views/CourseDetail'
import LibraryDetail from './views/LibraryDetail'
import ProjectDetail from './views/ProjectDetail'
import NewsDetail from './views/NewsDetail'
import NotFound from './views/NotFound'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/browse" element={<Browse />} />
          <Route path="/bootcamp/:slug" element={<BootcampDetail />} />
          <Route path="/path/:id" element={<PathDetail />} />
          <Route path="/course/:id" element={<CourseDetail />} />
          <Route path="/library/:id" element={<LibraryDetail />} />
          <Route path="/project/:id" element={<ProjectDetail />} />
          <Route path="/news/:id" element={<NewsDetail />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </App>
    </BrowserRouter>
  </React.StrictMode>,
)
