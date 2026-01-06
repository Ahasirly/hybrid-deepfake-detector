import { useState } from 'react'
import ImageUploader from './components/ImageUploader'
import ResultDisplay from './components/ResultDisplay'

function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-black mb-4">
            Hybrid Deepfake Detector
          </h1>
          <p className="text-xl text-gray-700">
            Deepfake detection using SBI, DistilDIRE, and ChatGPT Vision
          </p>
        </header>

        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8">
          <ImageUploader
            onResult={setResult}
            loading={loading}
            setLoading={setLoading}
          />

          {result && <ResultDisplay result={result} />}
        </div>

        <footer className="text-center mt-8 text-gray-600">
          <p>Using SBI, DistilDIRE, and ChatGPT Vision models</p>
        </footer>
      </div>
    </div>
  )
}

export default App
