import React from 'react';
import Link from 'next/link';

const Header = () => {
  return (
    <header className="bg-gray-800 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/" className="text-xl font-bold">
          CityPulse
        </Link>
        <nav>
          <Link href="/" className="px-3 hover:text-gray-300">
            Home
          </Link>
          <Link href="/submit-report" className="px-3 hover:text-gray-300">
            Submit Report
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
