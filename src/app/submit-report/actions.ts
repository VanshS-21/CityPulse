'use server';

export async function submitReport(prevState: { message: string; }, formData: FormData) {
  const rawFormData = {
    title: formData.get('title'),
    description: formData.get('description'),
    location: formData.get('location'),
    media: formData.get('media'),
  };

  // For now, we'll just log the data to the console.
  // In the future, this is where you would process the data, 
  // save it to a database, and handle file uploads.
  console.log(rawFormData);

  // You can return a response to the client, for example:
  return {
    message: 'Report submitted successfully!',
  };
}
