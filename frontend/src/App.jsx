import { BrowserRouter, Routes, Route } from "react-router-dom"
import Submit from "./pages/Submit"

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/submit/:token" element={<Submit />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
