export async function fetchApi(endpoint: string, method: string, data?: any) {
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000"; // Assuming backend runs on 8000


  const options: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(`${BACKEND_URL}${endpoint}`, options);


  if (!response.ok) {
    // If the response is not OK, try to parse error as JSON
    const errorData = await response.json();
    throw new Error(errorData.detail || "Something went wrong");
  }

  // For OK responses, return the raw Response object to allow streaming
  return response;
}
