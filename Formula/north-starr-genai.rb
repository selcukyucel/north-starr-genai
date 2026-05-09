class NorthStarrGenai < Formula
  desc "Your Development Partner — AI-specific workflow for AI coding tools"
  homepage "https://github.com/selcukyucel/north-starr-genai"
  url "https://github.com/selcukyucel/north-starr-genai/archive/refs/tags/v0.15.1.tar.gz"
  sha256 "43008f48156dd454f09031ff130f125a6ba4c44ea2e7920660cf7afb5bb7ae82"
  license "MIT"

  def install
    bin.install "bin/north-starr-genai"
    (share/"north-starr-genai").install "templates"
    (share/"north-starr-genai").install "skills"
  end

  test do
    system "#{bin}/north-starr-genai", "version"
  end
end
