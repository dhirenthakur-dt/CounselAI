import axios from 'axios';

const AI  = 'http://localhost:8001';

export const counselStudent = async (message) => {
  const res = await axios.post(`${AI}/counsel`, { message });
  return res.data;
};