class NorthStarrGenai < Formula
  desc "Your Development Partner — AI-specific workflow for AI coding tools"
  homepage "https://github.com/selcukyucel/north-starr-genai"
  url "https://github.com/selcukyucel/north-starr-genai/archive/refs/tags/v0.17.0.tar.gz"
  sha256 "764720a46cb6ab6622b1a8c2fef51774f52cceb7f39305be0dda8e03d19f79c7"
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
