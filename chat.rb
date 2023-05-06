class Chat < Formula
  include Language::Python::Virtualenv

  desc "Another GPT Wrapper"
  homepage "https://github.com/vidithbalasa/homebrew-chat"
  url "https://github.com/vidithbalasa/homebrew-chat/archive/refs/tags/v0.0.1.tar.gz"
  sha256 "ae29f73b396fd970f9c8fa8dd061ae0191ed6b0015f91efa7e88d9286fadbd68  homebrew-chat.tgz"
  license "Your project's license"

  depends_on "python@3.9"

  resource "openai" do
    url "https://files.pythonhosted.org/packages/41/85/5260c76a6a2b0e9c106c7716b21447c76162df2bc797bd411bf6ce63d2fd/openai-0.27.6.tar.gz"
    sha256 "63ca9f6ac619daef8c1ddec6d987fe6aa1c87a9bfdce31ff253204d077222375"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    # Your test instructions
  end
end
