const express = require('express');
const nodemailer = require('nodemailer');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

app.post('/subscribe', async (req, res) => {
  const { email } = req.body;

  const transporter = nodemailer.createTransport({
    host: 'smtp.zoho.eu',
    port: 465,
    secure: true,
    auth: {
      user: 'cs@fun-bet.me',
      pass: 'your_app_password' // Replace with your Zoho App Password
    }
  });

  const mailOptions = {
    from: 'cs@fun-bet.me',
    to: email,
    subject: '🎁 You’re In! Get Ready for Free Bonuses from FUN-BET.ME',
    text: `Thanks for signing up! As one of our early members, you'll receive exclusive free bonuses as soon as we launch. We're excited to have you on board — let the games begin!

— The FUN-BET.ME Team`,
  };

  try {
    await transporter.sendMail(mailOptions);
    res.status(200).send('Thanks for signing up!');
  } catch (error) {
    console.error('Error sending email:', error);
    res.status(500).send('Oops! Something went wrong.');
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));
