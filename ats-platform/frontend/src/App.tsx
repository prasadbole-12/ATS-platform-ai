import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from '@/components/layout/Layout'
import DashboardPage from '@/pages/DashboardPage'
import UploadResumePage from '@/pages/UploadResumePage'
import CandidatesPage from '@/pages/CandidatesPage'
import JobDescriptionsPage from '@/pages/JobDescriptionsPage'
import RankingsPage from '@/pages/RankingsPage'
import SettingsPage from '@/pages/SettingsPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/upload" element={<UploadResumePage />} />
            <Route path="/candidates" element={<CandidatesPage />} />
            <Route path="/jobs" element={<JobDescriptionsPage />} />
            <Route path="/rankings" element={<RankingsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
