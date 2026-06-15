import axios from 'axios';

const AI = 'http://localhost:8001';

export const counselStudent = async (message) => {
  const res = await axios.post(`${AI}/counsel`, { message });
  return res.data;
};

export const followUpQuestion = async (message, previousProfile, previousColleges) => {
  const res = await axios.post(`${AI}/follow-up`, {
    message,
    previous_profile: previousProfile,
    previous_colleges: previousColleges
  });
  return res.data;
};

export const getLiveCollegeDetails = async (college_name, college_id) => {
  const res = await axios.post(`${AI}/college/live-details`, { college_name, college_id });
  return res.data;
};

const API = 'http://localhost:8080/api';

export const getDistricts = async () => {
  const res = await axios.get(`${API}/colleges/districts`);
  return res.data;
};

export const searchColleges = async (query) => {
  const res = await axios.get(`${API}/colleges/search?query=${query}`);
  return res.data;
};

export const getCollegesByDistrict = async (district) => {
  const res = await axios.get(`${API}/colleges/district/${district}`);
  return res.data;
};

export const getCollegeCutoffs = async (id) => {
  const res = await axios.get(`${API}/colleges/${id}/cutoffs`);
  return res.data;
};