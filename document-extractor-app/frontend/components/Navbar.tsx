'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    if (path === '/home') {
      return pathname === '/home';
    }
    return pathname.startsWith(path);
  };

  return (
    <nav className="bg-white shadow-md border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo/Brand */}
          <Link href="/home" className="flex items-center space-x-2">
            <span className="text-xl font-bold text-blue-600">Document Extractor</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-4">
            <Link
              href="/documents"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/documents')
                  ? 'bg-blue-600 text-white font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Documents
            </Link>
            <Link
              href="/home"
              className={`px-4 py-2 rounded-lg transition-colors ${
                isActive('/home')
                  ? 'bg-blue-600 text-white font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Upload Files
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

