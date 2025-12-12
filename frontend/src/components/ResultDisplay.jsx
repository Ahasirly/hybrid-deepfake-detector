export default function ResultDisplay({ result }) {
  const isFake = result.is_fake
  const confidence = (result.confidence * 100).toFixed(2)

  return (
    <div className="mt-8 space-y-6">
      <div className="text-center">
        <div
          className={`inline-flex items-center justify-center w-32 h-32 rounded-full ${
            isFake ? 'bg-red-100' : 'bg-green-100'
          } mb-4`}
        >
          {isFake ? (
            <svg
              className="w-16 h-16 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          ) : (
            <svg
              className="w-16 h-16 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          )}
        </div>
        <h2 className={`text-3xl font-bold ${isFake ? 'text-red-600' : 'text-green-600'}`}>
          {isFake ? 'Deepfake Detected' : 'Authentic Image'}
        </h2>
        <p className="text-gray-600 mt-2 text-lg">
          Confidence: <span className="font-semibold">{confidence}%</span>
        </p>
      </div>

      {/* Model Details */}
      {result.models && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          {result.models.sbi && (
            <ModelCard
              name="SBI Model"
              isFake={result.models.sbi.is_fake}
              confidence={result.models.sbi.confidence}
            />
          )}
          {result.models.distildire && (
            <ModelCard
              name="DistilDIRE Model"
              isFake={result.models.distildire.is_fake}
              confidence={result.models.distildire.confidence}
            />
          )}
          {result.models.chatgpt && (
            <ModelCard
              name="ChatGPT Vision"
              isFake={result.models.chatgpt.is_fake}
              confidence={result.models.chatgpt.confidence}
            />
          )}
        </div>
      )}
    </div>
  )
}

function ModelCard({ name, isFake, confidence }) {
  return (
    <div className="bg-white rounded-lg p-4 border-2 border-gray-300">
      <h3 className="font-semibold text-black mb-2">{name}</h3>
      <div className={`text-sm font-medium ${isFake ? 'text-red-600' : 'text-green-600'}`}>
        {isFake ? 'Fake' : 'Authentic'}
      </div>
      <div className="text-sm text-gray-700 mt-1 font-medium">
        {(confidence * 100).toFixed(1)}%
      </div>
    </div>
  )
}
