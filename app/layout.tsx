import './globals.css';

export const metadata = {
  title: 'Stock Vision Predictor',
  description: 'AI Stock Chart Vision Predictor',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}