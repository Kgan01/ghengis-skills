import { HashRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { LiveMonitorPage } from './pages/LiveMonitorPage'
import { HistoryPage } from './pages/HistoryPage'
import { AgentDetailPage } from './pages/AgentDetailPage'
import { SearchPage } from './pages/SearchPage'
import { StatsPage } from './pages/StatsPage'
import { ProjectCardsPage } from './pages/ProjectCardsPage'
import ProjectSidebarPage from './pages/ProjectSidebarPage'
import { ProjectTimelinePage } from './pages/ProjectTimelinePage'

export default function App() {
  return (
    <HashRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<LiveMonitorPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="agent/:id" element={<AgentDetailPage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="stats" element={<StatsPage />} />
          <Route path="projects" element={<ProjectCardsPage />} />
          <Route path="projects/timeline" element={<ProjectTimelinePage />} />
          <Route path="projects/:name" element={<ProjectSidebarPage />} />
        </Route>
      </Routes>
    </HashRouter>
  )
}
