'use client';

import React, { useEffect, useRef } from 'react';
import { useFormState } from 'react-dom';
import { submitReport } from './actions';

const initialState = {
  message: '',
};

const SubmitReportPage = () => {
  const [state, formAction] = useFormState(submitReport, initialState);
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    if (state?.message) {
      alert(state.message);
      formRef.current?.reset();
    }
  }, [state]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Submit a New Report</h1>
      <form ref={formRef} action={formAction} className="bg-white p-6 rounded-lg shadow-md">
        <div className="mb-4">
          <label htmlFor="title" className="block text-gray-700 font-bold mb-2">Title</label>
          <input type="text" id="title" name="title" className="w-full px-3 py-2 border rounded-lg" placeholder="e.g., Pothole on Main St" required />
        </div>
        <div className="mb-4">
          <label htmlFor="description" className="block text-gray-700 font-bold mb-2">Description</label>
          <textarea id="description" name="description" rows={4} className="w-full px-3 py-2 border rounded-lg" placeholder="Provide details about the issue" required></textarea>
        </div>
        <div className="mb-4">
          <label htmlFor="location" className="block text-gray-700 font-bold mb-2">Location</label>
          <input type="text" id="location" name="location" className="w-full px-3 py-2 border rounded-lg" placeholder="e.g., 123 Main St, Anytown" required />
        </div>
        <div className="mb-4">
          <label htmlFor="media" className="block text-gray-700 font-bold mb-2">Upload Media</label>
          <input type="file" id="media" name="media" className="w-full px-3 py-2 border rounded-lg" />
        </div>
        <button type="submit" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg">
          Submit Report
        </button>
      </form>
    </div>
  );
};

export default SubmitReportPage;
