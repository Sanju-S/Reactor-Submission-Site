import { useState } from "react"
import { useNavigate } from "react-router-dom"
import api from "../api/client"

function Login() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const navigate = useNavigate()

  const login = () => {
    setError("")
    api.post("/auth/login", { username, password })
      .then(res => {
        localStorage.setItem("token", res.data.access_token)
        navigate("/dashboard")
      })
      .catch(() => {
        setError("Invalid credentials")
      })
  }

  return (
    <div className="page">
      <div className="container">
        <h2 className="title">Reactor Login</h2>

        <label>Username</label>
        <input value={username} onChange={e => setUsername(e.target.value)} />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
        />

        <button onClick={login}>Login</button>

        {error && <div className="message">{error}</div>}
      </div>
    </div>
  )
}

export default Login
