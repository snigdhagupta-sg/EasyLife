import axios from "axios";

export default axios.create({
  headers: { "Content-Type": "multipart/form-data" },
  baseURL: "http://localhost:8000",
  withCredentials: false,
});
