import { useEffect, useState } from "react"
import { useParams } from "react-router-dom"
import api from "../api/client"

function Submit() {
  const { token } = useParams()

  const [status, setStatus] = useState("loading")
  const [config, setConfig] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.get(`/submit/${token}`)
      .then(res => {
        if (res.data.status === "open") {
          setConfig(res.data)
          setStatus("open")
        } else {
          setStatus(res.data.status)
          setConfig(res.data)
        }
      })
      .catch(() => {
        setError("Invalid submission link")
        setStatus("error")
      })
  }, [token])

  if (status === "loading") return <h2>Loading…</h2>
  if (status === "error") return <h2>{error}</h2>

  if (status === "not_started") {
    return <h2>Submission opens at {config.start}</h2>
  }

  if (status === "closed") {
    return <h2>Submissions are closed. Stay tuned!</h2>
  }

//   return <SubmitForm token={token} config={config} />
  return (
    <div className="page">
      {status === "open" && (
        <SubmitForm token={token} config={config} />
      )}
    </div>
  )
}

function SubmitForm({ token, config }) {
  const [name, setName] = useState("")
  const [instagramId, setInstagramId] = useState("")
//   const [links, setLinks] = useState([""])
  const [wantsMoney, setWantsMoney] = useState(true)
  const [upiId, setUpiId] = useState("")
  const [message, setMessage] = useState("")
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)

  const [links, setLinks] = useState(() => {
        if (config.link_type === "fixed") {
            return Array(config.fixed_count).fill("")
        }
        return [""]
        })

  if (submitted) {
  return (
    <div className="container">
      <div className="success">
        <h2 className="success-title">🎉 Submission received!</h2>
        <p className="success-text">
          Thanks for participating.  
          Sit back and enjoy the stream.
        </p>
      </div>
    </div>
  )
}

  const maxLinks =
    config.link_type === "fixed"
      ? config.fixed_count
      : config.max_count

    // useEffect(() => {
    //     if (config.link_type === "fixed") {
    //     setLinks(Array(config.fixed_count).fill(""))
    //     }
    // }, [config])

  const addLink = () => {
    if (links.length < maxLinks) {
      setLinks([...links, ""])
    }
  }

  const updateLink = (i, value) => {
    const copy = [...links]
    copy[i] = value
    setLinks(copy)
  }

  const submit = () => {
    if (!name || !instagramId || links.some(l => !l)) {
      setMessage("Please fill all required fields")
      return
    }

    if (wantsMoney && !upiId) {
      setMessage("Please enter UPI ID")
      return
    }

    setLoading(true)

    api.post(`/submit/${token}`, {
      name,
      instagram_id: instagramId,
      links,
      wants_money: wantsMoney,
      upi_id: wantsMoney ? upiId : null
    })
    .then(() => {
        setMessage("")
      setSubmitted(true)
      setName("")
        setInstagramId("")
        setLinks([""])
        setUpiId("")
    })
    .catch(err => {
      setMessage(err.response?.data?.detail || "Submission failed")
    })
    .finally(() => setLoading(false))
  }

  return (
    <div className="container">
      <h2 className="title">Submit your entry</h2>

      <div>
        <label htmlFor="name"><b>Name (does not have to be actual government name)</b><span style={{ color: "red" }}>*</span></label><br />
        <input
            id="name"
            type="text"
            placeholder="Your name"
            value={name}
            onChange={e => setName(e.target.value)}
        />
        </div>

      <div>
        <label htmlFor="instagram"><b>Instagram ID</b><span style={{ color: "red" }}>*</span></label><br />
        <input
            id="instagram"
            type="text"
            placeholder="your_instagram_handle"
            value={instagramId}
            onChange={e => setInstagramId(e.target.value)}
        />
        </div>

        <p className="helper">
        {config.link_type === "fixed"
            ? `You must submit exactly ${config.fixed_count} links.`
            : `You can submit up to ${config.max_count} links.`}
        </p>
      <h4>Links <span style={{ color: "red" }}>*</span></h4>
      {links.map((link, i) => (
        <input
          key={i}
          placeholder={`Link ${i + 1}`}
          value={link}
          onChange={e => updateLink(i, e.target.value)}
        />
      ))}

      {config.link_type === "range" && links.length < maxLinks && (
        <button onClick={addLink}>Add link</button>
      )}

      <div className="radio-group">
        <label>
          <input
            type="radio"
            checked={wantsMoney}
            onChange={() => setWantsMoney(true)}
          />
          I want the money
        </label>

        <label>
          <input
            type="radio"
            checked={!wantsMoney}
            onChange={() => setWantsMoney(false)}
          />
          I'm here for fun
        </label>
      </div>

      {wantsMoney && (
        <input
          placeholder="UPI ID"
          value={upiId}
          onChange={e => setUpiId(e.target.value)}
        />
      )}

      <button onClick={submit} disabled={loading || submitted}>
        {loading ? "Submitting..." : "Submit"}
        </button>

      {message && <div className="message">{message}</div>}
    </div>
  )
}


export default Submit;