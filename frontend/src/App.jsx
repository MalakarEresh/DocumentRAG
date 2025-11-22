import { useState } from "react"
import axios from "axios"
import {
  Upload,
  FileText,
  Trash2,
  Calendar,
  X,
  Send,
  Loader2,
} from "lucide-react"

const API_BASE = "http://localhost:8000"

// Configure axios instance with credentials
const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // This ensures cookies are sent with every request
})

// Add request interceptor to log cookies
api.interceptors.request.use(
  (config) => {
    console.log(`[${config.method.toUpperCase()}] ${config.url}`)
    console.log("Cookies being sent:", document.cookie)
    return config
  },
  (error) => Promise.reject(error)
)

// Add response interceptor to log cookies
api.interceptors.response.use(
  (response) => {
    console.log("Response received, cookies now:", document.cookie)
    return response
  },
  (error) => Promise.reject(error)
)

function App() {
  const [file, setFile] = useState(null)
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [isAsking, setIsAsking] = useState(false)
  const [showBooking, setShowBooking] = useState(false)
  const [booking, setBooking] = useState({
    name: "",
    email: "",
    date: "",
    time: "10:00",
  })

  const handleFileSelect = (e) => {
    const selected = e.target.files?.[0]
    if (
      selected &&
      (selected.name.toLowerCase().endsWith(".pdf") ||
        selected.name.toLowerCase().endsWith(".txt"))
    ) {
      setFile(selected)
      setAnswer("")
    } else {
      alert("Please select a valid PDF or TXT file")
      e.target.value = null
    }
  }

  const uploadAndProcess = async () => {
    if (!file) return

    setIsProcessing(true)
    const formData = new FormData()
    formData.append("file", file)
    formData.append("chunking_strategy", "recursive")

    try {
      const response = await api.post("/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      console.log("✅ Upload response:", response.data)
      console.log("📌 Session ID from server:", response.data.session_id)
      setAnswer("Document processed successfully! You can now ask questions.")
      setFile(null)
    } catch (err) {
      console.error("❌ Upload error:", err.response?.data || err.message)
      setAnswer("Failed to upload document. Please try again.")
    } finally {
      setIsProcessing(false)
    }
  }

  const askQuestion = async () => {
    if (!question.trim()) return

    setIsAsking(true)
    try {
      const response = await api.post("/chat", { message: question.trim() })
      console.log("✅ Chat response:", response.data)
      console.log("📌 Session ID from server:", response.data.session_id)
      setAnswer(response.data.response || "No response received.")
    } catch (err) {
      console.error("❌ Chat error:", err.response?.data || err.message)
      setAnswer("Could not get answer. Make sure a document is uploaded.")
    } finally {
      setIsAsking(false)
      setQuestion("")
    }
  }

  const newChat = async () => {
    if (!confirm("Start fresh? This will remove the current document.")) return

    try {
      const response = await api.post("/new-chat")
      setAnswer("New session started. Upload a new document to begin.")
      setQuestion("")
      console.log("New chat response:", response.data)
    } catch (err) {
      console.error("New chat error:", err.response?.data || err.message)
      setAnswer("Session cleared.")
    }
  }

  const bookInterview = async (e) => {
    e.preventDefault()
    try {
      const response = await api.post("/book-interview", booking)
      alert(
        `Interview booked for ${booking.name} on ${booking.date} at ${booking.time}!`
      )
      setShowBooking(false)
      setBooking({ name: "", email: "", date: "", time: "10:00" })
      console.log("Booking response:", response.data)
    } catch (err) {
      console.error("Booking error:", err.response?.data || err.message)
      alert("Booking failed. Please check all fields.")
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto space-y-12">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Document Assistant
          </h1>
          <p className="text-gray-600">Upload your PDF/TXT and ask questions</p>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
            <FileText className="w-7 h-7 text-blue-600" />
            Upload Document
          </h2>

          <div className="space-y-6">
            <div className="border-2 border-dashed border-gray-300 rounded-xl p-10 text-center hover:border-blue-400 transition-colors">
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileSelect}
                className="hidden"
                id="file-input"
              />
              <label
                htmlFor="file-input"
                className="cursor-pointer block"
              >
                <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-medium">
                  Click to upload PDF or TXT
                </p>
                <p className="text-sm text-gray-500 mt-1">or drag and drop</p>
              </label>
            </div>

            {file && (
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <FileText className="w-10 h-10 text-blue-600" />
                    <div>
                      <p className="font-medium text-lg">{file.name}</p>
                      <p className="text-sm text-gray-600">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setFile(null)}
                    className="text-red-600 hover:bg-red-50 p-2 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <button
                  onClick={uploadAndProcess}
                  disabled={isProcessing}
                  className="w-full bg-blue-600 text-white py-3 rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2 transition-colors"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Processing Document...
                    </>
                  ) : (
                    "Process Document"
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Ask Question */}
        <div className="bg-white rounded-2xl shadow-lg p-8">
          <h2 className="text-2xl font-semibold mb-6">
            Ask About the Document
          </h2>
          <div className="space-y-4">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) =>
                e.key === "Enter" &&
                !e.shiftKey &&
                (e.preventDefault(), askQuestion())
              }
              placeholder="Type your question here..."
              rows={4}
              className="w-full p-4 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            />
            <div className="flex gap-3">
              <button
                onClick={askQuestion}
                disabled={isAsking || !question.trim()}
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                <Send className="w-5 h-5" />
                {isAsking ? "Thinking..." : "Ask"}
              </button>
              <button
                onClick={newChat}
                className="flex items-center gap-2 px-6 py-3 bg-red-600 text-white rounded-xl font-medium hover:bg-red-700 transition-colors"
              >
                <Trash2 className="w-5 h-5" />
                New Session
              </button>
            </div>

            {answer && (
              <div className="mt-6 p-6 bg-gray-50 border border-gray-200 rounded-xl">
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {answer}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Book Interview Button */}
        <div className="text-center">
          <button
            onClick={() => setShowBooking(true)}
            className="inline-flex items-center gap-3 px-8 py-4 bg-green-600 text-white text-lg font-semibold rounded-xl hover:bg-green-700 shadow-lg transition-all"
          >
            <Calendar className="w-6 h-6" />
            Book Interview Slot
          </button>
        </div>

        {/* Booking Modal */}
        {showBooking && (
          <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl p-8 max-w-md w-full shadow-2xl">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  Book Interview
                </h2>
                <button
                  onClick={() => setShowBooking(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              <form
                onSubmit={bookInterview}
                className="space-y-5"
              >
                <input
                  type="text"
                  placeholder="Full Name"
                  required
                  value={booking.name}
                  onChange={(e) =>
                    setBooking({ ...booking, name: e.target.value })
                  }
                  className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none"
                />
                <input
                  type="email"
                  placeholder="Email Address"
                  required
                  value={booking.email}
                  onChange={(e) =>
                    setBooking({ ...booking, email: e.target.value })
                  }
                  className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none"
                />
                <input
                  type="date"
                  required
                  value={booking.date}
                  onChange={(e) =>
                    setBooking({ ...booking, date: e.target.value })
                  }
                  className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none"
                />
                <select
                  value={booking.time}
                  onChange={(e) =>
                    setBooking({ ...booking, time: e.target.value })
                  }
                  className="w-full p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none"
                >
                  {[...Array(10)].map((_, i) => {
                    const hour = 9 + i
                    const timeStr = `${hour.toString().padStart(2, "0")}:00`
                    return (
                      <option
                        key={timeStr}
                        value={timeStr}
                      >
                        {timeStr}
                      </option>
                    )
                  })}
                </select>
                <button
                  type="submit"
                  className="w-full bg-green-600 text-white py-4 rounded-xl font-semibold hover:bg-green-700 transition-colors text-lg"
                >
                  Confirm Booking
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
