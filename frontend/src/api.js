import axios from 'axios';

const AI = 'http://localhost:8001';

export const counselStudent = async (message) => {
  const res = await axios.post(`${AI}/counsel`, { message });
  return res.data;
};

export const getLiveCollegeDetails = async (college_name, college_id) => {
  const res = await axios.post(`${AI}/college/live-details`, { college_name, college_id });
  return res.data;
};