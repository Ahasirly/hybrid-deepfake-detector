import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const detectDeepfake = async (imageFile) => {
  const formData = new FormData()
  formData.append('file', imageFile)

  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/detect`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    console.error('Detection error:', error)
    throw error
  }
}
