import unittest
from sectpl.token import Token, InvalidTokenException
import time


class Test(unittest.TestCase):
	"""Tests for STPL"""

	def test_secret_key(self):
		"""Make sure derived key is correct length"""
		self.assertEqual(len(Token._key), 32)
		self.assertEqual(len(Token._sig), 32)

	def test_pad_short(self):
		"""Make sure that short payload is 1 block long"""
		payload = 'AAAAA'
		self.assertEqual(len(Token._pad(payload)), 16)

	def test_pad_exact(self):
		"""Make sure that a payload exactly 32 bytes long is not padded"""
		payload = 'A'*32
		self.assertEqual(Token._pad(payload), payload)

	def test_encrypt_decrypt_user_prop(self):
		"""Make sure that we are able to recover all properties after decryption"""
		t = Token()
		p = ['a property', 'a second property']
		t.set(p)
		c = t.encrypt()
		self.assertEqual(Token.decrypt(c)[1:], p) #c[0] contains timestamp

	def test_encrypt_decrypt_user_prop_constructor(self):
		"""Make sure that we are able to recover all properties after decryption
		Use constructor.
		"""
		t = Token()
		p = ['a property', 'a second property']
		t.set(p)
		c = t.encrypt()
		self.assertEqual(Token(c).properties, p) #c[0] contains timestamp

	def test_timestamp(self):
		"""Make sure that timestamp is reasonable (this test could fail if machine hangs unreasonably so try re-running it if it does)"""
		t = Token()
		p = ['asdf']
		tt = int(time.time())
		t.set(p)
		self.assertTrue(t.timestamp -tt < 3)
		c = t.encrypt()
		tt = Token.decrypt(c)[0]
		self.assertEqual(t.timestamp, tt)

	def test_mangling(self):
		"""Make sure that if the IV in the ciphertext is tampered with, we are not able to recover any properties
		"""
		t = Token()
		t.set(['asdf'])
		c = t.encrypt()
		if c[0] != '0':
			c2 = '0' + c[1:]
		else:
			c2 = '1' + c[1:]
		self.assertRaises(InvalidTokenException, Token.decrypt, c2)	

	def test_mangling_2(self):
		"""Make sure that if some data is tampered with, we get an exception.
		"""
		t = Token()
		t.set(['asdf'])
		c = t.encrypt()
		if c[20] != '0':
			c2 = c[:20] + '0' + c[21:]
		else:
			c2 = c[:20] + '1' + c[21:]
		self.assertRaises(InvalidTokenException, Token.decrypt, c2)	

	def test_different_salts(self):
		"""Check that using different salts produces a different derived key"""
		Token.set_secret_keys('AAAAAAAA', ['000000','000000'])
		a = Token._key
		Token.set_secret_keys('AAAAAAAA', ['000001','000001'])
		b = Token._key
		self.assertTrue(a != b)

if __name__ == '__main__':
    Token.set_secret_keys('my_secret_key', ['XXXXXX','YYYYYY'])
    unittest.main()