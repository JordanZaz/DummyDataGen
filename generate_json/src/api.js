// api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://report.improvado.io/dummy-data',
  withCredentials: true
});

export default api;
