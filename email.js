export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method Not Allowed' });
  }

  const { email } = req.body;

  if (!email || !email.includes('@')) {
    return res.status(400).json({ message: 'Invalid email address' });
  }

  console.log(`Captured email: ${email}`);

  return res.status(200).json({ message: `Thanks! A welcome message is on its way to ${email}.` });
}
