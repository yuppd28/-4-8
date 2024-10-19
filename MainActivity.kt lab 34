package com.example.myapp

import android.graphics.Color
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import com.example.myapp.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val textViews = listOf(binding.tvName, binding.tvGroup, binding.tvCity)
        for (textView in textViews) {
            textView.setOnClickListener {
                textView.setTextColor(Color.RED)
            }
        }

        binding.btnHide.setOnClickListener {
            binding.tvHeader.visibility = View.INVISIBLE
        }

        binding.btnShow.setOnClickListener {
            binding.tvHeader.visibility = View.VISIBLE
        }
    }
}
