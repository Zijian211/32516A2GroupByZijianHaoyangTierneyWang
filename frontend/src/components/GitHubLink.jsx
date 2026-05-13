import React from "react";
import { Github } from "lucide-react";

export default function GitHubLink() {
  return (
    <a
      href="https://github.com/Zijian211/32516A2GroupByZijianHaoyangTierneyWang"
      target="_blank"
      rel="noopener noreferrer"
      className="relative bg-red-800 text-white p-2 sm:px-5 sm:py-2.5 rounded-full font-bold hover:bg-red-600 transition shadow-md flex items-center gap-2"
      title="View Source Code"
    >
      <Github size={20} />
      <span className="text-sm font-bold hidden md:inline">My GitHub</span>
    </a>
  );
}