class NorthStarrGenai < Formula
  desc "Your Development Partner — AI-specific workflow for AI coding tools"
  homepage "https://github.com/selcukyucel/north-starr-genai"
  url "https://github.com/selcukyucel/north-starr-genai/archive/refs/tags/v0.16.0.tar.gz"
  sha256 "68c5434ca13e37c5fd86f4c6f49408cb6fdee598ed7662577d48e526aa899941"
  license "MIT"

  def install
    bin.install "bin/north-starr-genai"
    (share/"north-starr-genai").install "templates"
    (share/"north-starr-genai").install "skills"
    (share/"north-starr-genai").install "references" if File.directory?("references")
  end

  test do
    system "#{bin}/north-starr-genai", "version"
  end
end
