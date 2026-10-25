import type { Metadata } from "next";import "./globals.css";
export const metadata:Metadata={title:"StudyForge — Learn by doing",description:"Turn notes into interactive practice and exams."};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
